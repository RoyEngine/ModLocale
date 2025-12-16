package second_in_command.skills.engineering

import com.fs.starfarer.api.Global
import com.fs.starfarer.api.campaign.comm.IntelInfoPlugin
import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.fleet.FleetMemberAPI
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.impl.campaign.intel.BaseIntelPlugin
import com.fs.starfarer.api.ui.SectorMapAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.skills.engineering.scripts.SolidConstructionScript
import second_in_command.specs.SCBaseSkillPlugin
import java.awt.Color

class SolidConstruction : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "舰队中所有舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("低战备状态导致负面影响的临界值降低至 30%% (基础值 50%%)", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("低战备状态导致故障的临界值降低至 24%% (基础值 40%%)", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("舰船不会再因为战斗而获得超过 2 个 D-插", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        //tooltip.addPara("   - Any additional d-mods after the first 2 are automatically removed after battle", 0f, Misc.getTextColor(), Misc.getHighlightColor())
        tooltip.addPara("   - 不会移除已拥有超过 2 个 D-插 之舰船上的 D-插，但会防止获得更多 D-插", 0f, Misc.getTextColor(), Misc.getHighlightColor())

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {
        stats!!.dynamic.getStat(Stats.CR_MALFUNCION_RANGE).modifyMult(id, 0.6f)
    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {

    }

    override fun advance(data: SCData, amount: Float) {

    }

    override fun onActivation(data: SCData) {
        if (data.isPlayer) {
            if (!Global.getSector().hasScript(SolidConstructionScript::class.java)) {
                Global.getSector().addScript(SolidConstructionScript())
            }
        }
    }

    override fun onDeactivation(data: SCData) {
        if (data.isPlayer) {
            for (script in ArrayList(Global.getSector().scripts)) {
                if (script is SolidConstructionScript) {
                    Global.getSector().removeScript(script)
                }
            }
        }
    }

}

class SolidConstructionIntel(var removed: ArrayList<Pair<String, String>>) : BaseIntelPlugin() {

    init {
        Global.getSector().addScript(this)
        endAfterDelay(7f)
    }

    override fun notifyEnded() {
        Global.getSector().removeScript(this)
    }

    override fun getName(): String {
        return "技能 - 坚固结构"
    }

    override fun getIcon(): String {
        return "graphics/secondInCommand/engineering/solid_construction.png"
    }

    override fun hasSmallDescription(): Boolean {
        return true
    }

    override fun createSmallDescription(info: TooltipMakerAPI, width: Float, height: Float) {
        info.addSpacer(3f)
        info.addPara("已避免某些星舰从最近的战斗遭遇中获得更多 D-插。", 0f, Misc.getTextColor(), Misc.getHighlightColor())
        info.addSpacer(10f)

        for ((ship, hullmod) in removed) {
            info.addPara("已避免 $ship 获得 $hullmod D-插", 3f, Misc.getTextColor(), Misc.getHighlightColor(), "$ship", "$hullmod")
        }

    }

    override fun addBulletPoints(info: TooltipMakerAPI, mode: IntelInfoPlugin.ListInfoMode?, isUpdate: Boolean, tc: Color?, initPad: Float) {
        //info!!.addPara("${pick.shipName} - removed ${spec.displayName}", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "${spec.displayName}")
        info.addPara("已避免某些星舰获得更多 D-插。", 0f, Misc.getTextColor(), Misc.getHighlightColor())
    }

    override fun getTitleColor(mode: IntelInfoPlugin.ListInfoMode?): Color {
        return Misc.getBasePlayerColor()
    }

    override fun getIntelTags(map: SectorMapAPI?): MutableSet<String> {
        var tags = super.getIntelTags(map)
        tags.add("Skills")
        return tags
    }
}