import type { CompanyView } from "../../api/views";

export function gathered(company: CompanyView): boolean {
    return company.seats.every((seated) => seated.claimed);
}
