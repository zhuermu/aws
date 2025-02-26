package com.zhuermu.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import java.util.List;
import java.util.Map;

@Data
public class Category {
    @JsonProperty("catetory1")
    private String category1;
    
    @JsonProperty("catetory2")
    private String category2;
    
    @JsonProperty("catetory3")
    private List<String> category3;

    @JsonProperty("weight")
    private Map<String, Integer> weight;
}
