import java.util.List;

public class Service {
    // Service (1) -> (0..*) LineService
    List<LineService> lineServices;

    // Service (1) -> (0..*) Cycle
    List<Cycle> cycles;
}
