/**
 * IO class for MiniRust runtime.
 * Provides input/output operations for MiniRust programs.
 */
public class io {
    // MiniRust specification functions
    public static void print_i32(int value) {
        System.out.print(value);
    }
    public static void println_i32(int value) {
        System.out.println(value);
    }
    public static void print_f32(float value) {
        System.out.print(value);
    }
    public static void println_f32(float value) {
        System.out.println(value);
    }
    public static void print_bool(boolean value) {
        System.out.print(value);
    }
    public static void println_bool(boolean value) {
        System.out.println(value);
    }
    public static void print_string(String value) {
        System.out.print(value);
    }
    public static void println_string(String value) {
        System.out.println(value);
    }
    public static void println() {
        System.out.println();
    }
}
