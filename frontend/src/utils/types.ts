//TODO: clean up types and import from prisma schema
interface User {
    id: number;
    email: string;
    name: string;
    linearId: number | null;
    slackId: string;
    rawMessages: any[] | null; // Replace `any` with appropriate type if available
    processedConversations: any[] | null; // Replace `any` with appropriate type if available
    tickets: any[] | null; // Replace `any` with appropriate type if available
    projects: any[] | null; // Replace `any` with appropriate type if available
}
