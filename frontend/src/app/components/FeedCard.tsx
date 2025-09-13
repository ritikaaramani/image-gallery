interface FeedCardProps {
  id: string;
  title: string;
  type: "image" | "album";
}

export default function FeedCard({ id, title, type }: FeedCardProps) {
  return (
    <div className="bg-white rounded-2xl shadow-md p-4 transition-transform transform hover:scale-105">
      <h3 className="text-lg font-semibold text-gray-800 mb-1 truncate">{title}</h3>
      <p className="text-gray-500 text-sm">{type}</p>
    </div>
  );
}
