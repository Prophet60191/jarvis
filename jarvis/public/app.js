// Import necessary libraries
import { render } from 'react-dom';

// Define the Portfolio component
class Portfolio extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            projects: [
                { title: "Project 1", description: "This is a project I worked on." },
                { title: "Project 2", description: "This is another project I worked on." }
            ]
        };
    }

    render() {
        return (
            <div>
                <h1>My Projects</h1>
                <ul>
                    {this.state.projects.map((project, index) => (
                        <li key={index}>
                            <h2>{project.title}</h2>
                            <p>{project.description}</p>
                        </li>
                    ))}
                </ul>
            </div>
        );
    }
}

// Render the Portfolio component to the DOM
render(<Portfolio />, document.getElementById('root'));
