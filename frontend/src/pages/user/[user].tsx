import Image from "next/image";
import { Inter } from "next/font/google";
import styled from "styled-components";
import { useState } from "react";
import { useRouter } from "next/router";
import { useQuery } from "@tanstack/react-query";
import { getChatResponse, getEmployee } from "../../utils/api";
import { EmployeeDetail } from "../../components/EmployeeDetail";

const inter = Inter({ subsets: ["latin"] });

const Container = styled.div``;
const MainContainer = styled.main``;

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
        <MainContainer className={`flex min-h-screen flex-col items-center justify-center p-24 ${inter.className}`}>
            <h2 className="text-xl"></h2>
            {isLoading || !userData ? <p>loading...</p> : <EmployeeDetail employee={userData}></EmployeeDetail>}
            <div className="py-2"></div>
            <ChatBox userId={userId as string} />
        </MainContainer>
    );
}

function ChatBox({ userId, userData }: { userId: string; userData: any }) {
    const [input, setInput] = useState("");
    const [output, setOutput] = useState("");
    const [history, setHistory] = useState<string[]>([]);

    // Make call to getChatResponse on submitHandler
    const submitHandler = () => {
        setHistory([...history, input]);
        setInput("");
        getChatResponse(userId, input).then((res) => {
            const data = res["summary"];
            console.log("data", data);
            setOutput(data);
        });
    };

    return (
        <Container className={`flex min-h-screen flex-col items-center justify-center${inter.className}`}>
            <h1 className="text-2xl font-bold">Chat</h1>
            {/* Input for chat */}
            <textarea
                value={input}
                onChange={(e) => {
                    setInput(e.target.value);
                }}
            />
            <button onClick={submitHandler}>Send</button>
            <div className="py-2 border-2 p-2">
                <h3 className="text-xl font-bold">Relevant Conversation</h3>
                {output && <p>{output}</p>}
            </div>
        </Container>
    );
}
