import Image from "next/image";
import { Inter } from "next/font/google";
import { getEmployees } from "../utils/api";
import { useQuery } from "@tanstack/react-query";
import styled from "styled-components";
import { EmployeeCard } from "../components/EmployeeCard";

const inter = Inter({ subsets: ["latin"] });

const Container = styled.main``;

export default function Home() {
    const { data: employees, isLoading } = useQuery<User[]>({ queryKey: ["employees"], queryFn: getEmployees });
    console.log(employees);
    return (
        <Container className={`flex min-h-screen flex-col items-center justify-center p-24 ${inter.className}`}>
            <h2 className="text-xl">
                <strong>Funnal</strong>
            </h2>
            <div className="py-2"></div>
            <h3>My employees</h3>
            {isLoading || !employees ? (
                <p>loading...</p>
            ) : (
                employees.map((employee, index) => <EmployeeCard employee={employee} key={index} />)
            )}
        </Container>
    );
}
