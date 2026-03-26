import { Link } from "react-router";

function NotFound() {
  return (
    <>
      <h1>404 Not Found</h1>
      <Link to={"/"}>
        <button>Back Home</button>
      </Link>
    </>
  );
}

export default NotFound;