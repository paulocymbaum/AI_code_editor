import React from 'react';
import './PricingCard.css';

interface PricingCardProps {
  title: string;
  price: number;
  features: string[];
  highlighted: boolean;
}

const PricingCard: React.FC<PricingCardProps> = ({ title, price, features, highlighted }) => {
  return (
    <div className={`pricing-card ${highlighted ? 'highlighted' : ''}`}> 
      <h2 className='title'>{title}</h2>
      <p className='price'>${price}</p>
      <ul className='features'>
        {features.map((feature, index) => (
          <li key={index}>
            <span className='checkmark' />
            {feature}
          </li>
        ))}
      </ul>
      <button className='call-to-action'>Sign up</button>
    </div>
  );
};

export default PricingCard;