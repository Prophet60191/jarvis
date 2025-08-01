// logger class to handle logging
class Logger {
    constructor() {
        this.console = console;
    }

    error(message, error) {
        this.console.error(message, error);
    }
}

export default Logger;
