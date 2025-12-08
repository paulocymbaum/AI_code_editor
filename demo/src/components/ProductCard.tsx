import React from 'react';

interface Product {
  id: number;
  name: string;
  price: number;
  description: string;
  image: string;
}

interface ProductCardProps {
  product: Product;
}

const ProductCard: React.FC<ProductCardProps> = ({ product }) => {
  return (
    <div className="max-w-sm mx-auto mt-10 bg-white rounded-xl shadow-md p-4 hover:shadow-lg">
      <img src={product.image} alt={product.name} className="w-full h-48 object-cover" />
      <h3 className="text-lg font-bold mt-4">{product.name}</h3>
      <p className="text-gray-600 mt-2">${product.price}</p>
      <p className="text-gray-600 mt-2">{product.description}</p>
      <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mt-4">Add to Cart</button>
    </div>
  );
};

export default ProductCard;