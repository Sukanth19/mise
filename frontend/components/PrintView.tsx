'use client';

import { Recipe } from '@/types';

interface PrintViewProps {
  recipe: Recipe;
}

export default function PrintView({ recipe }: PrintViewProps) {
  const imageUrl = recipe.image_url 
    ? `http://localhost:8000${recipe.image_url}` 
    : null;

  const handlePrint = () => {
    window.print();
  };

  return (
    <>
      {/* Print Button - Hidden in print mode */}
      <div className="print:hidden mb-6">
        <button
          type="button"
          onClick={handlePrint}
          className="comic-button px-6 py-3 bg-primary text-primary-foreground"
          aria-label="Print recipe"
        >
          🖨️ PRINT RECIPE
        </button>
      </div>

      {/* Print-optimized layout */}
      <div className="print-view">
        {/* Image */}
        {imageUrl && (
          <div className="mb-6">
            <img
              src={imageUrl}
              alt={recipe.title}
              className="w-full max-h-64 object-cover"
            />
          </div>
        )}

        {/* Title */}
        <h1 className="text-3xl font-black text-foreground mb-4 uppercase">
          {recipe.title}
        </h1>

        {/* Tags */}
        {recipe.tags && recipe.tags.length > 0 && (
          <div className="mb-6">
            <p className="text-sm text-muted-foreground">
              <strong>Tags:</strong> {recipe.tags.join(', ')}
            </p>
          </div>
        )}

        {/* Ingredients */}
        <div className="mb-6">
          <h2 className="text-2xl font-black text-foreground mb-3 uppercase">
            Ingredients
          </h2>
          <ul className="space-y-2">
            {recipe.ingredients.map((ingredient, index) => (
              <li key={index} className="flex items-start">
                <span className="mr-2">•</span>
                <span className="flex-1">{ingredient}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Steps */}
        <div className="mb-6">
          <h2 className="text-2xl font-black text-foreground mb-3 uppercase">
            Instructions
          </h2>
          <ol className="space-y-3">
            {recipe.steps.map((step, index) => (
              <li key={index} className="flex">
                <span className="flex-shrink-0 font-black mr-3">
                  {index + 1}.
                </span>
                <p className="flex-1">{step}</p>
              </li>
            ))}
          </ol>
        </div>

        {/* Reference Link */}
        {recipe.reference_link && (
          <div className="mt-6 text-sm text-muted-foreground">
            <p>
              <strong>Source:</strong> {recipe.reference_link}
            </p>
          </div>
        )}
      </div>

      {/* Print-specific styles */}
      <style jsx global>{`
        @media print {
          /* Hide navigation, buttons, and decorative elements */
          nav,
          header,
          footer,
          .comic-button,
          .print\\:hidden,
          button,
          [role="navigation"] {
            display: none !important;
          }

          /* Remove shadows and borders for cleaner print */
          .comic-panel,
          .comic-border {
            box-shadow: none !important;
            border: 1px solid #000 !important;
          }

          /* Optimize layout for print */
          body {
            background: white !important;
            color: black !important;
          }

          .print-view {
            max-width: 100% !important;
            margin: 0 !important;
            padding: 20px !important;
          }

          /* Ensure images fit on page */
          .print-view img {
            max-height: 300px !important;
            page-break-inside: avoid;
          }

          /* Prevent page breaks inside sections */
          .print-view h1,
          .print-view h2,
          .print-view h3 {
            page-break-after: avoid;
          }

          .print-view ul,
          .print-view ol {
            page-break-inside: avoid;
          }

          /* Readable font sizes */
          .print-view {
            font-size: 12pt;
            line-height: 1.5;
          }

          .print-view h1 {
            font-size: 24pt;
          }

          .print-view h2 {
            font-size: 18pt;
          }
        }
      `}</style>
    </>
  );
}
