import * as prismic from "@prismicio/client";
import * as prismicCustomTypes from "@prismicio/custom-types-client";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import fetch from "node-fetch";
import {
  API_KEY,
  WRITE_TOKEN,
  ACCESS_TOKEN,
  sourceRepositoryUrl,
  destinationRepositoryName,
  SHOULD_SYNC_CUSTOM_TYPES,
  CUSTOM_TYPE_NAME,
} from "./env";

/* --------------- Logging Setup --------------- */
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const logDirPath = path.join(__dirname, "./logs");
if (!fs.existsSync(logDirPath)) {
  fs.mkdirSync(logDirPath, { recursive: true });
}
const logFilePath = path.join(logDirPath, `${CUSTOM_TYPE_NAME}-migration.log`);
const logFileStream = fs.createWriteStream(logFilePath, { flags: "a" });
function logInfoConsole(...msgs: any[]) {
  console.log(...msgs);
}
function logErrorFile(...msgs: any[]) {
  const timestamp = new Date().toISOString();
  const messageStr = msgs
    .map((m) => (typeof m === "object" ? JSON.stringify(m) : m))
    .join(" ");
  console.error(messageStr);
  logFileStream.write(`[${timestamp}] ${messageStr}\n`);
}

/* --------------- Prismic / Fetch Config --------------- */
const srcRepositoryUrl = sourceRepositoryUrl;
function fetchWithTimeout(
  url: string,
  options: RequestInit = {},
  timeout: number = 10000,
): Promise<Response> {
  return new Promise((resolve, reject) => {
    const timeoutId = setTimeout(
      () => reject(new Error("Request timed out")),
      timeout,
    );
    fetch(url, options)
      .then((response) => resolve(response))
      .catch((error) => reject(error))
      .finally(() => clearTimeout(timeoutId));
  });
}
const customFetch: any = (url: string, options: RequestInit): Promise<Response> =>
  fetchWithTimeout(url, options, 20000);

/* --------------- Tracking & Global Sets --------------- */
const processedDocuments = new Set<string>();
const existingUIDs = new Set<string>();
const processedAssets = new Set<string>();

/* --------------- Allowed Headings --------------- */
const ALLOWED_HEADINGS = new Set([
  "paragraph",
  "preformatted",
  "heading2",
  "heading3",
  "heading4",
  "heading5",
  "strong",
  "em",
  "hyperlink",
  "embed",
  "list-item",
  "o-list-item",
  "rtl",
]);

/* --------------- UID Handling --------------- */
async function generateUniqueUID(document: any): Promise<string> {
  let baseUID = "";
  if (document.data?.title) {
    const rawTitle =
      typeof document.data.title === "string"
        ? document.data.title
        : prismic.asText(document.data.title);
    baseUID = rawTitle
      .toLowerCase()
      .trim()
      .replace(/\s+/g, "-")
      .replace(/[^a-z0-9-]/g, "")
      .replace(/^-+|-+$/g, "")
      .slice(0, 50);
  } else {
    baseUID = `uid-${Date.now()}`;
  }
  if (!baseUID) {
    baseUID = `uid-${Date.now()}`;
  }
  let uniqueUID = baseUID;
  let suffix = 1;
  while (existingUIDs.has(uniqueUID)) {
    uniqueUID = `${baseUID}-${suffix}`;
    suffix++;
  }
  existingUIDs.add(uniqueUID);
  return uniqueUID;
}

/* --------------- Type Checks --------------- */
function isImage(input: unknown): boolean {
  return (
    !!input &&
    typeof input === "object" &&
    (("url" in input &&
      typeof (input as any).url === "string" &&
      "dimensions" in input &&
      typeof (input as any).dimensions === "object") ||
      ("id" in input && (input as any).id?.asset?.url))
  );
}
function isMedia(input: unknown): boolean {
  return (
    !!input &&
    typeof input === "object" &&
    "link_type" in input &&
    (input as any).link_type === "Media"
  );
}

/* --------------- Link / Media Transform --------------- */
function transformLinkField(linkData: any): any | undefined {
  if (!linkData || typeof linkData !== "object") return linkData;
  if (linkData.link_type === "Media") {
    // If the existing id appears malformed (for example, ending with a dash), ignore it.
    let originalId = linkData.id;
    if (originalId && originalId.endsWith("-")) {
      originalId = "";
    }
    const mediaId =
      originalId && originalId.length > 0
        ? originalId
        : `media-${linkData.kind || "generic"}-${Date.now()}`;
    linkData.id = mediaId;
    // If URL is missing or still a placeholder, log and return undefined so the field is omitted.
    if (!linkData.url || linkData.url.includes("example.com/placeholder")) {
      logErrorFile(`Invalid or placeholder URL for media asset: ${mediaId}`);
      return undefined;
    }
    processedAssets.add(linkData.url);
    return linkData;
  } else if (linkData.link_type === "Document") {
    if (!linkData.id || typeof linkData.id !== "string") {
      const placeholderId = `doc-${Date.now()}`;
      logErrorFile(`Warning: Document link missing ID, using placeholder: ${placeholderId}`);
      linkData.id = placeholderId;
      linkData.type = linkData.type || "unknown_type";
      linkData.uid = linkData.uid || `placeholder-${placeholderId}`;
    }
    return linkData;
  }
  return linkData;
}

/* --------------- Migration / Normalization --------------- */
function fixHeadingType(type: string): string {
  return ALLOWED_HEADINGS.has(type) ? type : "paragraph";
}
function normalizeRichText(value: unknown): unknown[] {
  if (Array.isArray(value)) {
    return value
      .map((block) => {
        if (block && typeof block === "object" && "text" in block) {
          return {
            ...block,
            type: fixHeadingType((block as any).type || "paragraph"),
            spans: Array.isArray((block as any).spans) ? (block as any).spans : [],
          };
        }
        if (typeof block === "string") {
          return { type: "paragraph", text: block, spans: [] };
        }
        return undefined;
      })
      .filter((el) => el !== undefined);
  } else if (typeof value === "string" && value.trim() !== "") {
    return [{ type: "paragraph", text: value.trim(), spans: [] }];
  }
  return [];
}
function truncateAltText(input: any, maxLength = 500) {
  if (typeof input !== "string") {
    console.warn(`Invalid alt text encountered: ${input}`);
    return "No description provided";
  }
  if (input.length > maxLength) {
    console.warn(`Truncating alt text: ${input}`);
    return input.slice(0, maxLength);
  }
  console.warn(`Alt text length: ${input.length}`);
  return input;
}

/**
 * Recursively migrates document data. If a media field (such as productListPDF)
 * does not yield a valid link, its value will be undefined and later omitted.
 */
function migratePrismicDocumentData(
  input: unknown,
  context: { documentUid?: string; key?: string; parentKey?: string } = {},
): any {
  if (input === null || input === undefined) return undefined;
  if (isImage(input)) {
    try {
      return mapImageData(input, context);
    } catch (e) {
      console.error("Error mapping image data:", e);
      return undefined;
    }
  }
  if (isMedia(input)) {
    const inputObj = input as any;
    const mediaId = `media-${context.documentUid || ""}-${context.key || ""}-${
      inputObj.id || context.parentKey || ""
    }-${Date.now().toString() + Math.floor(Math.random() * 10000).toString()}`.replace(/undefined/g, "");
    const transformed = transformLinkField(inputObj);
    if (!transformed) {
      logErrorFile(
        `Skipping media field "${context.key}" for document "${context.documentUid}" due to invalid URL.`
      );
      return undefined;
    }
    return { ...transformed, alt: truncateAltText(inputObj.alt || ""), id: mediaId };
  }
  if (Array.isArray(input)) {
    return input
      .map((element) => migratePrismicDocumentData(element, context))
      .filter((el) => el !== undefined);
  }
  if (typeof input === "object") {
    const res: Record<string, unknown> = {};
    for (const key in input) {
      const migratedValue = migratePrismicDocumentData(input[key], {
        ...context,
        key,
        parentKey: context.key,
      });
      if (migratedValue !== undefined) {
        res[key] = migratedValue;
      }
    }
    return res;
  }
  return input;
}

/**
 * Helper: remove any keys with an undefined value.
 */
function removeEmptyFields(obj: any): any {
  if (Array.isArray(obj)) {
    return obj.map(removeEmptyFields).filter((v) => v !== undefined);
  } else if (obj !== null && typeof obj === "object") {
    const newObj: any = {};
    Object.keys(obj).forEach((key) => {
      const value = removeEmptyFields(obj[key]);
      if (value !== undefined) newObj[key] = value;
    });
    return newObj;
  }
  return obj === undefined ? undefined : obj;
}

/**
 * Creates a unique image ID based on context.
 */
function createUniqueImageId(
  image: any,
  context: { documentUid?: string; key?: string; parentKey?: string },
): string {
  const idParts = [
    "img",
    context.documentUid || "unknownDoc",
    context.key || "unknownKey",
    image.id?.asset?.id ||
      image.id?.originalField?.id ||
      image.id?.config?.id ||
      context.parentKey ||
      "noId",
    image.alt ? slugify(image.alt) : "no-alt",
    Date.now().toString(),
  ];
  return idParts.filter(Boolean).join("-").replace(/undefined/g, "");
}

/**
 * Extracts an image URL from several possible structures.
 */
function extractImageUrl(image: any): string {
  const urlCandidates = [
    image.url,
    image.id?.asset?.url,
    image.id?.config?.file,
    image.id?.originalField?.url,
  ];
  const url = urlCandidates.find((u) => typeof u === "string" && u.length > 0);
  if (!url) {
    console.warn("No valid image URL found:", image);
    return "";
  }
  return url;
}

/**
 * Transforms an image URL to a new domain.
 */
function transformImageUrl(url: string): string {
  if (!url) return "";
  try {
    new URL(url);
  } catch {
    console.warn("Invalid URL format:", url);
    return "";
  }
  if (url.includes("prismic.io")) {
    try {
      const urlParts = url.split("/");
      const filename = urlParts[urlParts.length - 1].split("?")[0];
      if (!filename) throw new Error("No filename found in URL");
      return `https://images.axa-contento-118412.eu/hk-axa-web-2020/${filename}`;
    } catch (e) {
      console.warn("Error transforming URL:", e);
      return url;
    }
  }
  return url;
}

/**
 * Maps image data to a consistent structure.
 */
function mapImageData(
  input: any,
  context: { documentUid?: string; key?: string; parentKey?: string },
): ImageOutput {
  if (!input) throw new Error("No image data provided");
  const imageId = createUniqueImageId(input, context);
  const originalUrl = extractImageUrl(input);
  const transformedUrl = transformImageUrl(originalUrl);
  if (!transformedUrl) throw new Error("Could not generate valid image URL");
  const dimensions = extractImageDimensions(input);
  if (!dimensions.width || !dimensions.height) {
    console.warn("Invalid image dimensions:", dimensions);
  }
  const alt = truncateAltText(input.alt || "");
  return {
    dimensions,
    alt,
    copyright: input.copyright || "",
    url: transformedUrl,
    id: imageId,
    edit: { zoom: 1, x: 0, y: 0, background: "transparent" },
  };
}

/**
 * Helper to slugify text.
 */
function slugify(text: string): string {
  return text
    .toString()
    .toLowerCase()
    .trim()
    .replace(/\s+/g, "-")
    .replace(/[^\w\-]+/g, "")
    .replace(/\-\-+/g, "-");
}

/**
 * Type definition for image output.
 */
interface ImageOutput {
  dimensions: { width: number; height: number };
  alt: string;
  copyright: string;
  url: string;
  id: string;
  edit: { zoom: number; x: number; y: number; background: string };
}

/**
 * Extracts image dimensions.
 */
function extractImageDimensions(image: any): { width: number; height: number } {
  const defaultDimensions = { width: 640, height: 480 };
  if (image.dimensions) return image.dimensions;
  if (image.id?.originalField?.dimensions) return image.id.originalField.dimensions;
  if (image.id?.asset) {
    return {
      width: image.id.asset.width || defaultDimensions.width,
      height: image.id.asset.height || defaultDimensions.height,
    };
  }
  return defaultDimensions;
}

/* --------------- Custom Types Setup --------------- */
const customTypesClient = prismicCustomTypes.createClient({
  repositoryName: destinationRepositoryName,
  token: WRITE_TOKEN,
  fetch: customFetch,
});
async function loadCustomTypesFiles(): Promise<any[]> {
  const directoryPath = path.join(__dirname, "../customtypes/enabled-ct");
  const files = fs.readdirSync(directoryPath).filter((file) => file.endsWith(".json"));
  const customTypes: any[] = [];
  for (const file of files) {
    const filePath = path.join(directoryPath, file);
    const fileContent = fs.readFileSync(filePath, "utf-8");
    const parsed = JSON.parse(fileContent);
    customTypes.push(parsed);
  }
  return customTypes;
}
async function syncCustomTypesWithDestRepo(customTypes: any[]): Promise<void> {
  const existingTypes = await customTypesClient.getAllCustomTypes();
  const existingIds = existingTypes.map((t) => t.id);
  for (const ct of customTypes) {
    if (existingIds.includes(ct.id)) {
      console.log(`Updating existing custom type: ${ct.id}`);
      await customTypesClient.updateCustomType(ct);
    } else {
      console.log(`Inserting new custom type: ${ct.id}`);
      await customTypesClient.insertCustomType(ct);
    }
  }
}
function transformSlice(slice: any) {
  if (slice.slice_type === "page") {
    slice.value = slice.value.map((item) => ({
      pageName: item.pageName || "Unnamed Page",
      pageUrl: item.pageUrl || "#",
      pageUrlGaAction: item.pageUrlGaAction || null,
    }));
  } else if (slice.slice_type === "subpage") {
    slice.value = slice.value.map((item) => ({
      subPageName: item.subPageName || "Unnamed Subpage",
      subPageUrl: item.subPageUrl || "#",
      subPageUrlGaAction: item.subPageUrlGaAction || null,
    }));
  } else {
    console.warn(`Unknown slice_type: ${slice.slice_type}`);
  }
  return slice;
}

/* --------------- Migration Logic --------------- */
async function processBatchOfDocuments(
  documents: any[],
  batchNumber: number,
  totalBatches: number,
): Promise<void> {
  const batchMigration = prismic.createMigration();
  let docsInBatch = 0;
  const batchDocuments = new Map<string, { id: string; uid: string; name: string }>();
  console.log(`\n--- Processing Batch ${batchNumber} of ${totalBatches}, size: ${documents.length} ---`);
  for (const document of documents) {
    console.log(`Processing doc ${document.id}...`);
    try {
      if (processedDocuments.has(document.id)) {
        console.log(`Skipping duplicate doc ${document.id}`);
        continue;
      }
      processedDocuments.add(document.id);
      console.log(`Document uid ${document.uid}...`);
      const uid = document.uid || (await generateUniqueUID(document));
      let documentName = "Untitled Document";
      if (typeof document.data.title === "string") {
        documentName = document.data.title;
      } else if (Array.isArray(document.data.title)) {
        documentName = prismic.asText(document.data.title) || "Untitled Document";
      }
      // Migrate the document data and clean it from empty (undefined) fields.
      const migratedData = removeEmptyFields(migratePrismicDocumentData(document.data, { documentUid: document.uid }));
      const updatedDocument: any = { ...document, uid, data: migratedData };
      batchDocuments.set(document.id, { id: document.id, uid, name: documentName });
      batchMigration.createDocumentFromPrismic(updatedDocument, documentName);
      docsInBatch++;
    } catch (err: any) {
      const errorContext = { documentId: document.id, documentUid: document.uid, error: err.message };
      console.log("Error:: ", JSON.stringify(errorContext));
      logErrorFile(`Error preparing doc ${document.id} for migration: ${err.message}`);
    }
  }
  if (docsInBatch > 0) {
    const writeClient = prismic.createWriteClient(destinationRepositoryName, {
      writeToken: WRITE_TOKEN,
      migrationAPIKey: API_KEY,
    });
    try {
      await writeClient.migrate(batchMigration, {
        reporter: (event: any) => {
          console.log(JSON.stringify(event, null, 2));
          if (event.type === "documents:updated") {
            logErrorFile("Document updated", JSON.stringify(event, null, 2));
          }
          if (event.type === "documents:updating") {
            logErrorFile("Document updating", JSON.stringify(event, null, 2));
          }
        },
      });
    } catch (migrationError: any) {
      const failedBatchDetails = {
        batchNumber,
        totalDocuments: docsInBatch,
        documents: Array.from(batchDocuments.values()),
        error: {
          message: migrationError.message || "Unknown error",
          response: migrationError.response,
          url: migrationError.url,
        },
      };
      logErrorFile(`Migration Error in batch ${batchNumber}:`, JSON.stringify(failedBatchDetails, null, 2));
    }
  } else {
    console.log(`No documents in this batch to migrate.`);
  }
}

(async function main() {
  try {
    if (SHOULD_SYNC_CUSTOM_TYPES) {
      console.log("Loading custom types...");
      const allCustomTypes = await loadCustomTypesFiles();
      console.log("Loaded custom types. Syncing with destination repo...");
      await syncCustomTypesWithDestRepo(allCustomTypes);
    } else {
      console.log("Skipping custom type synchronization.");
    }
    const sourceClient = prismic.createClient(`${srcRepositoryUrl}/api/v2`, {
      accessToken: ACCESS_TOKEN,
    });
    console.log(`Retrieving documents from ${srcRepositoryUrl}...`);
    let allDocs;
    try {
      allDocs = await sourceClient.getAllByType(`${CUSTOM_TYPE_NAME}`);
      console.log(`Total documents retrieved: ${allDocs.length}`);
    } catch (error: any) {
      logErrorFile(`Failed to retrieve documents: ${error.message}`);
      throw error;
    }
    console.log(`Total documents retrieved: ${allDocs.length}`);
    const batchSize = 50;
    let currentIndex = 0;
    let batchNumber = 1;
    const totalBatches = Math.ceil(allDocs.length / batchSize);
    while (currentIndex < allDocs.length) {
      const batchDocs = allDocs.slice(currentIndex, currentIndex + batchSize);
      await processBatchOfDocuments(batchDocs, batchNumber, totalBatches);
      currentIndex += batchSize;
      batchNumber++;
    }
    console.log(`\n=== Migration Finished! ===`);
    console.log(`Total documents attempted: ${allDocs.length}`);
    logErrorFile(`\n=== Final Migration Summary ===`);
    logErrorFile(`Total docs: ${allDocs.length}`);
    if (processedAssets.size > 0) {
      logErrorFile(`\n=== Processed Assets ===`);
      for (const url of processedAssets) {
        logErrorFile(`- ${url}`);
      }
    }
    console.log(`\nAll done.`);
    process.exit(0);
  } catch (err: any) {
    logErrorFile("Fatal error in migration script:", err);
    if (err.response) {
      logErrorFile("Error response:", {
        status: err.response.status,
        statusText: err.response.statusText,
        body: await err.response.text().catch(() => "Unable to read response body"),
      });
    }
    process.exit(1);
  }
})();
