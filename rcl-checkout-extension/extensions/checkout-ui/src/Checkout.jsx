import '@shopify/ui-extensions/preact';
import { render } from "preact";
import { useState } from "preact/hooks";

export default async () => {
  render(<TCKimlikField />, document.body);
};

function TCKimlikField() {
  const initial = shopify.attributes?.current?.["TC Kimlik No"] ?? "";
  const [value, setValue] = useState(initial);
  const [error, setError] = useState("");

  async function handleInput(event) {
    const raw = event.target.value.replace(/\D/g, "").slice(0, 11);
    setValue(raw);
    if (raw.length > 0 && !/^[1-9][0-9]{10}$/.test(raw)) {
      setError("Geçerli TC Kimlik No giriniz: 11 rakam, 0 ile başlamaz");
    } else {
      setError("");
    }
    await shopify.applyAttributeChange({
      type: "updateAttribute",
      key: "TC Kimlik No",
      value: raw,
    });
  }

  return (
    <s-text-field
      label="TC Kimlik No"
      value={value}
      max-length={11}
      inputmode="numeric"
      error={error || undefined}
      onInput={handleInput}
    />
  );
}
