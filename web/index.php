<?php

$danger_status_file =
    "/home/strawberry/safe_cycling_project/runtime/danger_status.json";


/*
 * Diese Anfrage liest nur den aktuellen Danger-Status.
 */
if (isset($_GET["check_danger"]))
{
    $danger = false;

    clearstatcache(true, $danger_status_file);

    if (is_readable($danger_status_file))
    {
        $content = file_get_contents($danger_status_file);
        $status = json_decode($content, true);

        if (
            is_array($status) &&
            isset($status["danger"]) &&
            $status["danger"] === true
        )
        {
            $danger = true;
        }
    }

    header("Content-Type: application/json");
    header("Cache-Control: no-store, no-cache, must-revalidate");

    echo json_encode([
        "danger" => $danger
    ]);

    exit;
}


/*
 * Ursprünglicher funktionierender START-Befehl.
 *
 * Er läuft im versteckten iframe, sodass die sichtbare
 * Webseite nicht blockiert wird.
 */
if (isset($_POST["start"]))
{
    echo shell_exec(
        "cd /home/strawberry/safe_cycling_project && " .
        "WEB_START=1 python3 main.py 2>&1"
    );

    exit;
}


/*
 * Messung stoppen.
 */
if (isset($_POST["stop"]))
{
    shell_exec(
        "pkill -2 -f 'python3 main.py'"
    );

    exit;
}

?>

<!DOCTYPE html>
<html>

<head>

    <title>Safe Cycling Control</title>

    <style>

        body {
            background: #1e1e1e;
            color: white;
            font-family: Arial;
            text-align: center;
            margin-top: 100px;
        }

        button {
            width: 220px;
            height: 100px;
            font-size: 30px;
            border: none;
            border-radius: 20px;
            margin: 20px;
            color: white;
            cursor: pointer;
        }

        .start {
            background: green;
        }

        .stop {
            background: red;
        }

        .control-form {
            display: inline-block;
        }

        #danger-box {
            width: 500px;
            height: 150px;
            margin: 40px auto;
            border-radius: 20px;
            background: green;
        }

        #danger-box.danger {
            background: red;
        }

        /*
         * Die iframes führen START und STOP aus,
         * sollen aber nicht sichtbar sein.
         */
        .hidden-frame {
            display: none;
        }

    </style>

</head>

<body>

<h1>Safe Cycling Project</h1>

<div id="danger-box"></div>


<!-- START läuft im unsichtbaren start-frame. -->
<form
    method="post"
    target="start-frame"
    class="control-form"
>
    <button
        type="submit"
        class="start"
        name="start"
    >
        START
    </button>
</form>


<!-- STOP läuft unabhängig im unsichtbaren stop-frame. -->
<form
    method="post"
    target="stop-frame"
    class="control-form"
>
    <button
        type="submit"
        class="stop"
        name="stop"
    >
        STOP
    </button>
</form>


<iframe
    name="start-frame"
    class="hidden-frame"
></iframe>

<iframe
    name="stop-frame"
    class="hidden-frame"
></iframe>


<script>

const dangerBox =
    document.getElementById("danger-box");


async function checkDanger()
{
    try
    {
        const response = await fetch(
            "index.php?check_danger=1&t=" + Date.now(),
            {
                cache: "no-store"
            }
        );

        if (!response.ok)
        {
            throw new Error("Status request failed");
        }

        const result = await response.json();

        if (result.danger === true)
        {
            dangerBox.classList.add("danger");
        }
        else
        {
            dangerBox.classList.remove("danger");
        }
    }
    catch (error)
    {
        console.log(
            "Danger-Status konnte nicht gelesen werden.",
            error
        );
    }
    finally
    {
        /*
         * Nach 200 ms erneut prüfen.
         * Dadurch entstehen keine überlappenden Anfragen.
         */
        setTimeout(checkDanger, 200);
    }
}


checkDanger();

</script>

</body>

</html>
