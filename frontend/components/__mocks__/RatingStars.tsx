export default function RatingStars({ value, onChange, readOnly }: any) {
  return (
    <div data-testid="rating-stars" data-value={value} data-readonly={readOnly}>
      {!readOnly && onChange && (
        <button onClick={() => onChange(5)}>Rate 5 stars</button>
      )}
    </div>
  );
}
