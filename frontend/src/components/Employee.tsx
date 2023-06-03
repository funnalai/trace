import styled from "styled-components";

const Container = styled.div`
    padding: 1rem;
    border-radius: 0.5rem;
    cursor: grab;
    &:hover {
        background-color: #f5f5f5;
    }
`;

export const EmployeeCard = ({ employee }: { employee: User }) => {
    return (
        <Container>
            <p>{employee.name}</p>
        </Container>
    );
};
