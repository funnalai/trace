export async function getEmployees() {
    const result = await fetch(process.env.NEXT_PUBLIC_API_URL + "/users");
    const json = await result.json();
    return json;
}

export async function getEmployee(id: string) {
    const result = await fetch(process.env.NEXT_PUBLIC_API_URL + `/user?id=${encodeURIComponent(id)}`);
    const json = await result.json();
    return json;
}
