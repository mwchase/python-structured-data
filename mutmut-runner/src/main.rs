use std::error::Error;

fn modified_files() -> std::io::Result<Vec<String>> {
    let mut files = vec![];
    let stdout = String::from_utf8(std::process::Command::new("hg").arg("status").arg("--modified").output()?.stdout);
    match stdout {
        Ok(string) => for line in string.lines() {
            if line.len() > 0 {
                files.push(String::from(&line[2..]))
            }
        },
        Err(_) => (),
    }
    Ok(files)
}

fn cache_file(file: &String) -> Option<String> {
    let path = std::path::Path::new(file);
    let mut cache_dir = std::path::PathBuf::from(path.parent()?);
    cache_dir.push("__pycache__");
    let mut prefix = String::from(path.file_stem()?.to_str()?);
    prefix.push('.');
    for entry in std::fs::read_dir(cache_dir).ok()? {
        if let Ok(dir_entry) = entry {
            if let Some(file_name) = dir_entry.file_name().to_str() {
                if file_name.starts_with(&prefix) {
                    match dir_entry.path().to_str() {
                        Some(string) => return Some(String::from(string)),
                        None => (),
                    }
                }
            }
        }
        unimplemented!()
    }
    None
}

fn test_file(file: &String) -> Option<String> {
    let path = std::path::Path::new(file);
    let parent = path.parent()?.strip_prefix("src").ok()?;
    let mut file_name = String::from("test_");
    file_name.push_str(path.file_name()?.to_str()?);
    let mut backup_path = String::from(file);
    backup_path.push_str(".bak");
    if !std::path::Path::new(&backup_path).exists() {
        return None
    }
    let mut test_path = std::path::PathBuf::from("tests");
    test_path.push(parent);
    test_path.push(file_name);
    test_path.to_str().map(String::from)
}

fn run_in_venv(exe: &str, args: &Vec<String>) -> std::io::Result<std::process::Output> {
    let mut bin = String::from(".nox/mutmut_install/bin/");
    bin.push_str(exe);
    std::process::Command::new(bin).args(args).output()
}

fn remove_files(files: &Vec<String>) -> std::io::Result<()> {
    for file in files.iter() {
        let remove_result = std::fs::remove_file(file);
        if let Err(error) = remove_result {
            if error.kind() != std::io::ErrorKind::NotFound {
                return Err(error)
            }
        }
    }
    Ok(())
}

fn main() -> Result<(), Box<dyn Error>> {
    run_in_venv("mypy", &vec![String::from("src/structured_data")])?;

    let m_files = modified_files()?;

    let cache_files = m_files.iter().filter_map(cache_file).collect();
    if remove_files(&cache_files).is_err() {
        return Ok(())
    }

    let test_result = run_in_venv("pytest", &std::iter::once(String::from("-vv")).chain(m_files.iter().filter_map(test_file)).collect());

    if remove_files(&cache_files).is_err() {
        return Ok(())
    }

    test_result?;
    Ok(())
}
