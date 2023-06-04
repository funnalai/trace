import Image from "next/image";
import { JetBrains_Mono } from "next/font/google";
import styled from "styled-components";
import { useState } from "react";
import { useRouter } from "next/router";
import { useQuery } from "@tanstack/react-query";
import { getChatResponse, getEmployee } from "../../utils/api";
import { EmployeeDetail } from "../../components/EmployeeDetail";
import BounceLoader from "react-spinners/BounceLoader";
import Link from "next/link";

const jbm = JetBrains_Mono({ subsets: ["latin"] });

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
        <MainContainer>
            {/* Back to home Link */}
            <div className="fixed top-5 left-5">
                <Link href="/" className={`text-blue-500 text-sm ${jbm.className}`}>
                    Back to Home
                </Link>
            </div>
            <Container className={`flex min-h-screen flex-col items-center justify-center p-24 ${jbm.className}`}>
                <h2 className="text-xl"></h2>
                {isLoading || !userData ? <p>loading...</p> : <EmployeeDetail employee={userData}></EmployeeDetail>}
            </Container>
            <ChatBox userId={userId as string} />
        </MainContainer>
    );
}

function ChatBox({ userId }: { userId: string }) {
    const [input, setInput] = useState("");
    const [output, setOutput] = useState("");
    const [history, setHistory] = useState<string[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    // Make call to getChatResponse on submitHandler
    const submitHandler = () => {
        setHistory([...history, input]);
        setInput("");
        setIsLoading(true);
        getChatResponse(userId, input).then((res) => {
            const data = res["summary"];
            console.log("data", data);
            setOutput(data);
            setIsLoading(false);
        });
    };
    // Stick chatbox to bottom right of page, set background to gray
    return (
        // Set max width to 400px
        <Container
            className={`fixed bottom-5 right-5 p-4 border-2 border-gray-300 bg-gray-100 rounded-md ${jbm.className} shadow-md w-96`}
        >
            <h1 className={`font-bold pb-2`}>Ask me about anything</h1>
            <div className="flex flex-col items-center justify-center">
                <textarea
                    style={{
                        outline: "none",
                        padding: "0.5rem",
                        fontSize: "0.75rem",
                        resize: "none",
                        border: "2px solid #cbd5e1",
                        borderRadius: "0.5rem",
                    }}
                    className="w-full"
                    value={input}
                    onChange={(e) => {
                        setInput(e.target.value);
                    }}
                />
                <button onClick={submitHandler} className="bg-blue-400 text-white p-1 mt-2 rounded-md">
                    Send
                </button>
                <div className="py-2"></div>
                {isLoading && <BounceLoader color={"#60a5fa"} size={30} />}
                {output && !isLoading && (
                    <div className="py-2 border-2 p-2 mb-4 ">
                        <h3 className="font-bold">Most Relevant Conversation → </h3>
                        <TextDisplay text={output} />
                    </div>
                )}
            </div>
        </Container>
    );
}

function TextDisplay({ text }: { text: string }) {
    const [showMore, setShowMore] = useState(false);

    if (text.length < 100) {
        return <p className="text-sm">{text}</p>;
    }
    if (showMore) {
        return (
            <div>
                <p className="text-sm">{text}</p>
                <button onClick={() => setShowMore(false)} className=" text-sm text-blue-600">
                    Show Less
                </button>
            </div>
        );
    }
    return (
        <div>
            <p className="text-sm">{text.slice(0, 100)}...</p>
            <button onClick={() => setShowMore(true)} className=" text-sm text-blue-600">
                Show More
            </button>
        </div>
    );
}
