import Image from "next/image";
import { useQuery } from "react-query";
import { getEmployees } from "../utils/api";

export default function Home() {
    const { employees, isLoading, refetch } = useQuery<User[]>("employees", getEmployees);
    console.log(employees);
    return (
        <main className="flex min-h-screen flex-col items-center justify-between p-24">
            <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm lg:flex">
                <h2>My employees</h2>
            </div>
        </main>
    );
}
