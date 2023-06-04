import styled from "styled-components";

const Container = styled.div`
    width: 100%;
    a {
        text-decoration: none;
        color: white !important;
    }
`;

export const EmployeeDetail = ({ employee }: { employee: User }) => {
    // display employee details
    return (
        <Container>
            <p className="font-bold text-xl pb-4">{employee.name}
                <span className="text-gray-400 text-sm">
                {" "} | {employee.email}
                </span>
            </p>
            <div className="border-2 border-gray-300 p-4">
                <h2 className="text-xl font-bold pb-2">What {employee.name} Talked About This Week</h2>
                <iframe style={{}} srcDoc={employee.timeGraphHTML} width="100%" height="500px"></iframe>
                <iframe srcDoc={employee.clustersGraph} width="100%" height="500px"></iframe>
            </div>
        </Container>
    );
};
