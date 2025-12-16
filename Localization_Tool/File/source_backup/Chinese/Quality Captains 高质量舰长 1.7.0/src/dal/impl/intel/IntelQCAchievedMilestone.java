package dal.impl.intel;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.characters.FullName;
import com.fs.starfarer.api.characters.PersonAPI;
import com.fs.starfarer.api.impl.campaign.ids.Skills;
import com.fs.starfarer.api.impl.campaign.intel.BaseIntelPlugin;
import com.fs.starfarer.api.ui.Alignment;
import com.fs.starfarer.api.ui.SectorMapAPI;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import com.fs.starfarer.api.util.Misc;

import dal.impl.campaign.skills.milestones.CaptainsUnbound;

import java.awt.*;
import java.io.IOException;
import java.util.LinkedHashSet;
import java.util.Set;

public class IntelQCAchievedMilestone extends BaseIntelPlugin {

	private String name;
	private String icon;

    public IntelQCAchievedMilestone(String skillIcon, String skillName) {
		try {
			Global.getSettings().loadTexture(skillIcon);
		} catch (IOException e) {
			
		}
        this.name = skillName;
        this.icon = skillIcon;
        //runcode dal.plugins.Captains_Utils.debugAwardMilestones();
    }

    @Override
    protected String getName() {
        return "已达成里程碑: " + name;
    }

    @Override
    protected void addBulletPoints(TooltipMakerAPI info, ListInfoMode mode, boolean isUpdate, Color tc, float initPad) {

        Color gray = Misc.getGrayColor();

        info.addSpacer(3f);
        info.addPara("打开角色界面查看效果", 0f, gray, gray);
    }

    @Override
    public void createSmallDescription(TooltipMakerAPI info, float width, float height) {
    	Color gray = Misc.getGrayColor();
        info.addSpacer(10f);
        TooltipMakerAPI imageTooltip = info.beginImageWithText(icon, 64f);
        imageTooltip.addPara("达成重大里程碑后，你将获得一项全新的永久技能。", 0f);
        info.addImageWithText(0f);

        info.addSpacer(10f);

        info.addPara("在 QC 中，所有技能 (包括增益效果) 均可通过 LunaLib 在游戏过程中进行配置。", 0f);
        info.addPara("若未使用 LL，或希望配置文件自动加载，相同选项可在 data/config/LunaSettings.csv 中找到。", 0f, gray, gray);
    }

    @Override
    public String getIcon() {
        return icon;
    }

    @Override
    public Set<String> getIntelTags(SectorMapAPI map) {
        Set<String> tags = new LinkedHashSet<String>();

        //tags.add("Milestones");

        return tags;
    }
}
