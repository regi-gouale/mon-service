// Use type safe message keys from the French messages (source of truth)
import fr from "../messages/fr.json";

type Messages = typeof fr;

declare global {
  // Use type safe message keys with `next-intl`
  // eslint-disable-next-line @typescript-eslint/no-empty-object-type
  interface IntlMessages extends Messages {}
}
