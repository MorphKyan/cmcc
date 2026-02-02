
try {
    const inputs = [
        '/api',
        'http://localhost:8000/api',
        'https://example.com/api',
        'domain.com/api',
        undefined,
        null,
        ''
    ];

    console.log("Testing URL parsing...");

    inputs.forEach(input => {
        try {
            console.log(`Input: "${input}"`);
            const urlObj = new URL(input);
            console.log(`  -> Valid. Host: ${urlObj.host}, Path: ${urlObj.pathname}`);
        } catch (e) {
            console.log(`  -> Error: ${e.message}`);
        }
    });

} catch (err) {
    console.error(err);
}
