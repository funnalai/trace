export async function getEmployees() {
    const result = await fetch(process.env.NEXT_PUBLIC_API_URL + "/users");
    const json = await result.json();
    return json;
}
