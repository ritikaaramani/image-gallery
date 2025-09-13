interface UploadCardProps {
  id: string;
  filename: string;
  mime_type: string;
}

export default function UploadCard({ id, filename, mime_type }: UploadCardProps) {
  return (
    <div className="bg-white rounded-2xl shadow-md p-4 transition-transform transform hover:scale-105">
      <h3 className="text-lg font-semibold text-gray-800 mb-1 truncate">{filename}</h3>
      <p className="text-gray-500 text-sm">{mime_type}</p>
    </div>
  );
}
