interface UserCardProps {
  id: string;
  username: string;
  email?: string;
}

export default function UserCard({ id, username, email }: UserCardProps) {
  return (
    <div className="bg-white rounded-2xl shadow-md p-4 transition-transform transform hover:scale-105">
      <h3 className="text-lg font-semibold text-gray-800 mb-1 truncate">{username}</h3>
      {email && <p className="text-gray-500 text-sm">{email}</p>}
    </div>
  );
}
