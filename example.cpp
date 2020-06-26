/** 
 * This is a 
 * multiline 
 * comment
 */
class ExampleClass {
public:
    //* Single line comment
    ExampleClass(int x = 42);
    
    //! Multiple
    //  Single
    //  Line
    //  Comments
    bool returnsTrue(void *data);
    auto returnsFalse() -> bool; //< End of line comment
    
    int returnsTheTruth() { return 42; }
};

bool ExampleClass::returnsTrue(void *) { return true; }
