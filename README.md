# HTTP Benchw

**HTTP Benchw** is a lightweight HTTP load testing tool designed to help evaluate 
the performance of web applications or proxies under various load conditions. 
It supports comprehensive performance testing of both HTTP endpoints and HTTP 
proxy servers, with full support for HTTP proxy credential's authentication. 
The tool enables multiprocess testing for enhanced performance evaluation, 
allows custom host header configuration, and provides test duration as a 
limiting factor for controlled testing scenarios.

## Installation

You can install HTTP Benchw using pip:

```bash
git clone https://github.com/rrguardo/httpbenchw.git
pip install -e .
```

## Usage

### Running a Benchmark

To run a benchmark, execute the `httpbenchw_test` command with the desired arguments.

```bash
httpbenchw_test --url http://your-api-url.com/api/status --proxy-ip 192.168.1.1 --proxy-port 8080 --use-proxy True --timeout 15 --host-header your-host-header --process-count 4 --test-duration 30
```

### Output

HTTP Benchw will output the results of the benchmark, including:

- Number of requests completed
- Average response time
- Median response time
- Fastest response
- Slowest response
- Status codes breakdown
- Errors
- Requests per second

## Contributing

Contributions to HTTP Benchw are welcome. Please follow these steps to contribute:

1. Fork the repository on GitHub.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with descriptive messages.
4. Push your changes to your forked repository.
5. Submit a pull request.

## License

**HTTP Benchw** is open-source software licensed under the 
GNU General Public License v3.0 (GPLv3). You can view the full license text at 
[https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html).
