interface AlbumCardProps {
  id: string;
  title: string;
  images_count: number;
}

export default function AlbumCard({ id, title, images_count }: AlbumCardProps) {
  return (
    <div className="bg-white rounded-2xl shadow-md p-4 transition-transform transform hover:scale-105">
      <h3 className="text-lg font-semibold text-gray-800 mb-2 truncate">{title}</h3>
      <p className="text-gray-500 text-sm">{images_count} images</p>
    </div>
  );
}
