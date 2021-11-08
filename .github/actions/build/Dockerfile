FROM rust:latest

RUN cargo install mdbook --no-default-features --features output
RUN cargo install mdbook-toc
RUN cargo install mdbook-epub
RUN cargo install mdbook-open-on-gh

CMD ["mdbook", "build"]