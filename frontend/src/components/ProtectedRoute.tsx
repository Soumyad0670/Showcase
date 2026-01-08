import { Navigate } from "react-router-dom";
import { auth } from "@/lib/firebase";

export const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
    // Check if a token exists or if Firebase has an active user
    const token = localStorage.getItem("token");

    if (!token) {
        return <Navigate to="/login" replace />;
    }

    return <>{children}</>;
};
