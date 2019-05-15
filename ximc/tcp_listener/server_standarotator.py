


  def gerätpos         }

    print("\nRead position")
    x_pos = get_position_t()
    result = lib.get_position(device_id, byref(x_pos))
    print("Result: " + repr(result))
    if result == Result.Ok:
        print("Position: " + repr(x_pos.Position))
    return x_pos.Position

