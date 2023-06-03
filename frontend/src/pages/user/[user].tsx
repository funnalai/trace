import Image from "next/image";
import { Inter } from "next/font/google";
import styled from "styled-components";
import { useRouter } from "next/router";
import { useQuery } from "@tanstack/react-query";
import { getEmployee } from "../../utils/api";
import { EmployeeDetail } from "../../components/EmployeeDetail";

const inter = Inter({ subsets: ["latin"] });

const Container = styled.main``;

export default function User() {
    const router = useRouter();
    const userId = router.query.user;
    const { data: userData, isLoading } = useQuery<User>({
        queryKey: ["user", `${userId}`],
        queryFn: () => getEmployee(`${userId}`),
        enabled: userId !== undefined,
    });
    console.log(userData);
    return (
        <Container className={`flex min-h-screen flex-col items-center justify-center p-24 ${inter.className}`}>
            <h2 className="text-xl">
                {isLoading || !userData ? <p>loading...</p> : <EmployeeDetail employee={userData}></EmployeeDetail>}
            </h2>
            <div className="py-2"></div>
        </Container>
    );
}
