#!/bin/bash

# Fix Demo Page - Update page.tsx to use existing components
# This script updates the demo page to use components that actually exist

set -e

echo "🔧 Fixing Demo Page Imports..."

# Path to the page file
PAGE_FILE="demo/src/app/page.tsx"

# Create new page content with existing components
cat > "$PAGE_FILE" << 'EOF'
import React from 'react';
import HeroSection from '../components/HeroSection';
import FeatureCard from '../components/FeatureCard';
import PricingCard from '../components/PricingCard';
import CTAButton from '../components/CTAButton';

const features = [
  {
    icon: '⚡',
    title: 'Lightning Fast',
    description: 'Built for speed and performance with modern optimization techniques'
  },
  {
    icon: '🎨',
    title: 'Beautiful Design',
    description: 'Professionally crafted components following design system principles'
  },
  {
    icon: '🔧',
    title: 'Easy to Use',
    description: 'Simple, intuitive API that gets you up and running in minutes'
  },
  {
    icon: '🚀',
    title: 'Production Ready',
    description: 'Battle-tested components used by thousands of developers'
  },
  {
    icon: '♿',
    title: 'Accessible',
    description: 'WCAG compliant with full keyboard navigation and screen reader support'
  },
  {
    icon: '📱',
    title: 'Responsive',
    description: 'Works perfectly on all devices from mobile to desktop'
  }
];

const pricingPlans = [
  {
    title: 'Starter',
    price: 0,
    period: 'forever',
    features: [
      'Up to 3 projects',
      'Basic components',
      'Community support',
      'Regular updates'
    ],
    highlighted: false
  },
  {
    title: 'Professional',
    price: 29,
    period: 'month',
    features: [
      'Unlimited projects',
      'All components',
      'Priority support',
      'Advanced features',
      'Custom themes',
      'Team collaboration'
    ],
    highlighted: true
  },
  {
    title: 'Enterprise',
    price: 99,
    period: 'month',
    features: [
      'Everything in Pro',
      'Dedicated support',
      'Custom development',
      'SLA guarantee',
      'Training & onboarding',
      'White-label option'
    ],
    highlighted: false
  }
];

const Page = () => {
  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Hero Section */}
      <HeroSection />
      
      {/* Features Section */}
      <section className="section bg-white">
        <div className="container">
          <div className="text-center mb-12">
            <h2 className="section-title">
              Why Choose Our Platform
            </h2>
            <p className="section-subtitle">
              Everything you need to build amazing applications
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
            {features.map((feature, index) => (
              <FeatureCard 
                key={index}
                icon={feature.icon}
                title={feature.title}
                description={feature.description}
              />
            ))}
          </div>
        </div>
      </section>
      
      {/* Pricing Section */}
      <section className="section">
        <div className="container">
          <div className="text-center mb-12">
            <h2 className="section-title">
              Simple, Transparent Pricing
            </h2>
            <p className="section-subtitle">
              Choose the plan that's right for you
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8 max-w-6xl mx-auto">
            {pricingPlans.map((plan, index) => (
              <PricingCard 
                key={index}
                title={plan.title}
                price={plan.price}
                period={plan.period}
                features={plan.features}
                highlighted={plan.highlighted}
              />
            ))}
          </div>
        </div>
      </section>
      
      {/* CTA Section */}
      <section className="section bg-primary-600 text-white">
        <div className="container text-center">
          <h2 className="text-4xl font-bold mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-xl mb-8 text-primary-100">
            Join thousands of developers building amazing things
          </p>
          <div className="flex gap-4 justify-center">
            <CTAButton />
            <button className="btn-outline border-white text-white hover:bg-white hover:text-primary-600 btn-lg">
              View Documentation
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Page;
EOF

echo "✅ Page updated successfully!"
echo ""
echo "📝 Updated components used:"
echo "  - HeroSection"
echo "  - FeatureCard"
echo "  - PricingCard"
echo "  - CTAButton"
echo ""
echo "🚀 Now you can run: cd demo && npm run dev"
