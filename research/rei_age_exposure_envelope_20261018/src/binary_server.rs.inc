    if binary_rpc {
        use std::io::{Read, Write};
        io::stdout().flush()?;
        let mut input = io::stdin().lock();
        let mut output = io::stdout().lock();
        loop {
            let mut tag = [0u8; 1];
            match input.read(&mut tag) {
                Ok(0) => break,
                Ok(1) => {},
                Ok(_) => unreachable!("one-byte tag buffer"),
                Err(error) if error.kind() == io::ErrorKind::Interrupted => continue,
                Err(error) => return Err(error.into()),
            }
            let mut word = [0u8; 4];
            input.read_exact(&mut word)?;
            let active = u32::from_le_bytes(word) as usize;
            let mut real = [0u8; 8];
            input.read_exact(&mut real)?;
            let x = f64::from_le_bytes(real);
            input.read_exact(&mut word)?;
            let len = u32::from_le_bytes(word) as usize;
            if len != 4 + 2 * birth_count * cells + EXTRA {
                return Err("binary RHS state length mismatch".into());
            }
            let mut z = Vec::with_capacity(len);
            for _ in 0..len {
                input.read_exact(&mut real)?;
                z.push(f64::from_le_bytes(real));
            }
            let result: Result<Vec<u8>, Box<dyn std::error::Error>> = match tag[0] {
                b'R' => evaluate(&s, active, x, &z).map(|v| {
                    v.iter().flat_map(|r| r.to_le_bytes()).collect::<Vec<_>>()
                }),
                b'P' => physical(&s, active, x, &z).map(String::into_bytes),
                _ => Err("invalid binary RPC mode".into()),
            };
            let (status, payload) = match result {
                Ok(payload) => (0u8, payload),
                Err(error) => (1u8, format!("ERR {error:?}").into_bytes()),
            };
            let size = u32::try_from(payload.len())?;
            output.write_all(&[status])?;
            output.write_all(&size.to_le_bytes())?;
            output.write_all(&payload)?;
            output.flush()?;
        }
        return Ok(());
    }
