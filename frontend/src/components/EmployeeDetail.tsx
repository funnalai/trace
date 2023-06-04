import styled from "styled-components";

const Container = styled.div`
    width: 100%;
`;

export const EmployeeDetail = ({ employee }: { employee: User }) => {
    // display employee details
    return (
        <Container>
            <p>{employee.name}</p>
            <p>{employee.email}</p>
            <iframe srcDoc={employee.timeGraphHTML} width="100%" height="500px"></iframe>
            <div className="py-4"></div>
        </Container>
    );
};
