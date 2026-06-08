interface UserAvatarProps {
    readonly avatar_url: string | undefined
    readonly name: string
}

function UserAvatar({ avatar_url, name = "?" } : UserAvatarProps){
  return (
    <>
      {avatar_url
        ? <img
          src={avatar_url}
          alt={name}
          className="w-8 h-8 rounded-full object-cover shrink-0"
        />
        : <div className="w-8 h-8 rounded-full bg-linear-to-br from-emerald-400 to-cyan-5000 flex items-center justify-center text-xs font-bold text-text shrink-0">
          {name.charAt(0).toUpperCase()}
        </div>
      }
    </>
  );
}

export default UserAvatar;
