import React from 'react';
import ProductCard from '../components/ProductCard';

const products = [
  { name: 'Laptop', price: 99, image: 'https://example.com/laptop.jpg', description: 'This is a laptop' },
  { name: 'Phone', price: 99, image: 'https://example.com/phone.jpg', description: 'This is a phone' },
  { name: 'Tablet', price: 99, image: 'https://example.com/tablet.jpg', description: 'This is a tablet' },
  { name: 'Watch', price: 99, image: 'https://example.com/watch.jpg', description: 'This is a watch' },
  { name: 'Headphones', price: 99, image: 'https://example.com/headphones.jpg', description: 'These are headphones' },
  { name: 'Camera', price: 99, image: 'https://example.com/camera.jpg', description: 'This is a camera' }
];

const Page = () => {
  return (
    <div className="container mx-auto p-4 pt-6 mt-10">
      <h1 className="text-3xl font-bold">Products Catalog</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3 gap-4">
        {products.map((product) => (
          <ProductCard key={product.name} product={product} />
        ))}
      </div>
    </div>
  );
};

export default Page;