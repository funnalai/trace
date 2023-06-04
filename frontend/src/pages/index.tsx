import Image from "next/image";
import { JetBrains_Mono } from "next/font/google";
import { getEmployees } from "../utils/api";
import { useQuery } from "@tanstack/react-query";
import styled from "styled-components";
import { EmployeeCard } from "../components/EmployeeCard";

const jbm = JetBrains_Mono({ subsets: ["latin"] });

const Container = styled.main``;

export default function Home() {
    const { data: employees, isLoading } = useQuery<User[]>({ queryKey: ["employees"], queryFn: getEmployees });
    // console.log(employees);
    return (
        <Container className={`flex min-h-screen flex-col justify-center p-24 pt-4 ${jbm.className}`}>
            <h2 className="text-4xl font-bold pb-2 border-b-2 border-gray-600">
                Funnal<span className="text-blue-500">.ai</span>
            </h2>
            <div className="py-2"></div>
            <h3 className="text-2xl font-bold text-gray-600 pb-2">My Employees</h3>
            {isLoading ? (
                <p className="font-bold text-gray-400">loading...</p>
            ) : (
                employees.map((employee, index) => <EmployeeCard employee={employee} key={index} />)
            )}
        </Container>
    );
}
