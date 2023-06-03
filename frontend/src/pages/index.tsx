import Image from "next/image";
import { Inter } from "next/font/google";
import { getEmployees } from "../utils/api";
import { useQuery } from "@tanstack/react-query";

const inter = Inter({ subsets: ["latin"] });

export default function Home() {
    const { data: employees, isLoading } = useQuery<User[]>({ queryKey: ["employees"], queryFn: getEmployees });
    console.log(employees);
    return (
        <main className={`flex min-h-screen flex-col items-center justify-center p-24 ${inter.className}`}>
            <h2 className="text-xl">Funnal</h2>
            <h3>My employees</h3>
            {isLoading || !employees ? (
                <p>loading...</p>
            ) : (
                employees.map((employee, index) => (
                    <div style={{ margin: 0, padding: 0 }} key={index}>
                        <p>{employee.name}</p>
                    </div>
                ))
            )}
        </main>
    );
}
