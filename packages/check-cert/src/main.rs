// Copyright (C) 2023 Checkmk GmbH - License: GNU General Public License v2
// This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
// conditions defined in the file COPYING, which is part of this source code package.

use anyhow::Result;
use check_cert::{check, checker, fetcher};
use clap::Parser;
use std::time::Duration as StdDuration;
use time::{Duration, Instant};
use x509_parser::certificate::X509Certificate;
use x509_parser::prelude::FromDer;

#[derive(Parser, Debug)]
#[command(about = "check_cert")]
struct Args {
    /// URL to check
    #[arg(short, long)]
    url: String,

    /// Port
    #[arg(short, long, default_value_t = 443)]
    port: u16,

    /// Set timeout in seconds
    #[arg(long, default_value_t = 10)]
    timeout: u64,

    /// Expected serial
    #[arg(long)]
    pub serial: Option<String>,

    /// Expected subject
    #[arg(long)]
    pub subject: Option<String>,

    /// Expected issuer
    #[arg(long)]
    pub issuer: Option<String>,

    /// Warn if certificate expires in n days
    #[arg(long, default_value_t = 30)]
    not_after_warn: u32,

    /// Crit if certificate expires in n days
    #[arg(long, default_value_t = 0)]
    not_after_crit: u32,

    /// Warn if response time is higher (milliseconds)
    #[arg(long, default_value_t = 60_000)]
    response_time_warn: u32,

    /// Crit if response time is higher (milliseconds)
    #[arg(long, default_value_t = 90_000)]
    response_time_crit: u32,

    /// Disable SNI extension
    #[arg(long, action = clap::ArgAction::SetTrue)]
    disable_sni: bool,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = Args::parse();

    let Ok(not_after_levels) = check::LowerLevels::try_new(
        args.not_after_warn * Duration::DAY,
        args.not_after_crit * Duration::DAY,
    ) else {
        check::Output::bail_out("invalid args: not after crit level larger than warn");
    };

    let Ok(response_time_levels) = check::UpperLevels::try_new(
        args.response_time_warn * Duration::MILLISECOND,
        args.response_time_crit * Duration::MILLISECOND,
    ) else {
        check::Output::bail_out("invalid args: response time crit higher than warn");
    };

    let start = Instant::now();
    let der = fetcher::fetch_server_cert(
        &args.url,
        &args.port,
        if args.timeout == 0 {
            None
        } else {
            Some(StdDuration::new(args.timeout, 0))
        },
        !args.disable_sni,
    )?;
    let response_time = start.elapsed();

    let (_rem, cert) = X509Certificate::from_der(&der)?;
    let out = check::Output::from(vec![
        checker::check_response_time(response_time, response_time_levels),
        checker::check_details_serial(cert.tbs_certificate.raw_serial_as_string(), args.serial)
            .unwrap_or_default(),
        checker::check_details_subject(cert.tbs_certificate.subject(), args.subject)
            .unwrap_or_default(),
        checker::check_details_issuer(cert.tbs_certificate.issuer(), args.issuer)
            .unwrap_or_default(),
        checker::check_validity_not_after(
            cert.tbs_certificate.validity().time_to_expiration(),
            not_after_levels,
            cert.tbs_certificate.validity().not_after,
        ),
    ]);
    println!("HTTP {}", out);
    out.bye()
}
