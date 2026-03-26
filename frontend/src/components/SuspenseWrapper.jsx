import PropTypes from "prop-types";
import { Suspense } from "react";

function SuspenseWrapper({ children }) {
  return (
    <Suspense fallback={<h1>Loading...</h1>}>
      {children}
    </Suspense>
  );
}

SuspenseWrapper.propTypes = {
  children: PropTypes.node
};

export default SuspenseWrapper;