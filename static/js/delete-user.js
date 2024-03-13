async function deleteUser(user_id) {
    try {
        const response = await fetch(
            `/delete_user/${user_id}`,
            { method: "DELETE" }
        )

        if (!response.ok) {
            throw new Error(`Response status code is ${response.status}`)
        }

        location.href = '/login'

    } catch (error) {
        console.error(error)
    }
}