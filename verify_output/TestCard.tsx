import React;

interface TestCardProps {
  title: string;
  description: string;
}

const TestCard = (props: TestCardProps) => {
  return (
    <div className="p-4">
      <h1>TestCard</h1>
      {/* Add your component logic here */}
    </div>
  );
};

export default TestCard;
