/** Reads a text field. FormData can also hold File values, which are not text. */
export function readField(formData: FormData, name: string): string {
  const value = formData.get(name);
  return typeof value === "string" ? value : "";
}
