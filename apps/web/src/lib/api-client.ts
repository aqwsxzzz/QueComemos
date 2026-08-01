import { z } from "zod";

const API_URL = import.meta.env["VITE_API_URL"] ?? "http://localhost:8000/api/v1";

/** The API's error envelope: { detail, code, errors? }. */
const apiErrorSchema = z.object({
  detail: z.string(),
  code: z.string(),
  errors: z.array(z.object({ field: z.string(), message: z.string() })).optional(),
});

export interface FieldError {
  field: string;
  message: string;
}

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly fieldErrors: FieldError[];

  constructor(status: number, code: string, detail: string, fieldErrors: FieldError[]) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.fieldErrors = fieldErrors;
  }
}

export interface RequestOptions {
  method?: "GET" | "POST" | "PATCH" | "PUT" | "DELETE";
  body?: unknown;
  token?: string | null;
  signal?: AbortSignal;
}

async function toApiError(response: Response): Promise<ApiError> {
  const parsed = apiErrorSchema.safeParse(await response.json().catch(() => null));
  if (!parsed.success) {
    return new ApiError(response.status, "unknown_error", "Algo salió mal. Probá de nuevo.", []);
  }
  const { detail, code, errors } = parsed.data;
  return new ApiError(response.status, code, detail, errors ?? []);
}

/**
 * The API is a separate service: its shape is not guaranteed by the compiler,
 * so every response is validated here at the boundary before it reaches a hook.
 */
export async function request<T>(
  path: string,
  schema: z.ZodType<T>,
  options: RequestOptions = {},
): Promise<T> {
  const { method = "GET", body, token, signal } = options;

  const response = await fetch(`${API_URL}${path}`, {
    method,
    signal,
    headers: {
      ...(body === undefined ? {} : { "Content-Type": "application/json" }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });

  if (!response.ok) {
    throw await toApiError(response);
  }
  if (response.status === 204) {
    return schema.parse(undefined);
  }
  return schema.parse(await response.json());
}

/**
 * Multipart upload. The Content-Type header is deliberately omitted so the
 * browser sets it with the multipart boundary.
 */
export async function uploadFile<T>(
  path: string,
  schema: z.ZodType<T>,
  form: FormData,
  token: string,
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: form,
  });

  if (!response.ok) {
    throw await toApiError(response);
  }
  return schema.parse(await response.json());
}
