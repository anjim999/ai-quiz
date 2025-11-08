import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="max-w-3xl mx-auto text-center pt-12">
      <img
        src="https://i.pravatar.cc/120"
        className="mx-auto rounded-full shadow mb-6"
        alt="profile"
      />
      <h1 className="text-3xl font-bold mb-2">DeepKlarity AI Exam System</h1>
      <p className="text-gray-600 mb-6">
        Generate quizzes from Wikipedia and take secure, timed exams.
      </p>
      <Link to="/app" className="btn btn-primary">
        Take Quiz
      </Link>
    </div>
  );
}
