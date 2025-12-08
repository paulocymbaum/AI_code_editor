import React from 'react';

interface PricingCardProps {
  title: string;
  price: string;
  features: string[];
}

const PricingCard: React.FC<PricingCardProps> = ({ title, price, features }) => {
  return (
    <div className="max-w-sm mx-auto mt-10 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
      <p className="text-lg font-bold text-gray-600">${price}/month</p>
      <ul>
        {features.map((feature, index) => (
          <li key={index} className="text-lg text-gray-600">
            {feature}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default PricingCard;